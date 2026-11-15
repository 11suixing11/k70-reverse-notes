"""Run small, architecture-specific operations with the installed reverse libraries."""
import json
from pathlib import Path
import capstone
import unicorn
import z3
import pefile
from elftools.elf.elffile import ELFFile

code = bytes.fromhex("200580d2")  # mov x0, #41
decoder = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
instructions = [{"mnemonic": i.mnemonic, "operands": i.op_str} for i in decoder.disasm(code, 0x1000)]
assert instructions and instructions[0]["mnemonic"] == "mov"
emulator = unicorn.Uc(unicorn.UC_ARCH_ARM64, unicorn.UC_MODE_ARM)
emulator.mem_map(0x1000, 0x1000)
emulator.mem_write(0x1000, code)
emulator.emu_start(0x1000, 0x1004)
register = emulator.reg_read(unicorn.arm64_const.UC_ARM64_REG_X0)
assert register == 41
x = z3.BitVec("x", 32)
solver = z3.Solver()
solver.add((x ^ 0x1337) + 7 == 7)
assert solver.check() == z3.sat
solution = solver.model()[x].as_long()
assert solution == 0x1337
sample_dir = Path(__file__).resolve().parent
pe = pefile.PE(str(sample_dir / "reverse-pe.exe"))
assert pe.FILE_HEADER.Machine == 0x8664
exports = [entry.name.decode() for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols]
assert "reverse_check" in exports
with (sample_dir / "reverse-linux-arm64").open("rb") as stream:
    elf = ELFFile(stream)
    assert elf.header["e_machine"] == "EM_AARCH64"
print(json.dumps({"capstone": instructions, "unicorn_x0": register,
                  "z3_solution": solution, "pe_machine": "AMD64", "pe_exports": exports,
                  "elf_machine": "AArch64", "passed": True}, indent=2))
