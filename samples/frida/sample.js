import Java from 'frida-java-bridge';
Java.perform(() => {
    const Lab = Java.use('dev.k70.reverselab.MainActivity');
    const method = Lab.reverseCheck.overload('int');
    method.implementation = function (value) {
        const original = method.call(this, value);
        send({ hook: 'reverseCheck', input: value, original: original });
        return 42;
    };
    const result = Lab.reverseCheck(0x1337);
    send({ test: 'java-hook', result: result });
});
