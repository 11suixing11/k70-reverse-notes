package dev.k70.reverselab;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Button;

public class MainActivity extends Activity {
    public static int reverseCheck(int value) {
        return (value ^ 0x1337) + 7;
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(56, 160, 56, 56);
        layout.setBackgroundColor(Color.rgb(245, 247, 250));
        TextView title = new TextView(this);
        title.setText("K70 Reverse Lab");
        title.setTextSize(28);
        title.setTextColor(Color.rgb(25, 35, 50));
        layout.addView(title);
        TextView details = new TextView(this);
        details.setText("Local sample for JADX, apktool and Frida.\n\nreverseCheck(0x1337) = " + reverseCheck(0x1337) + "\n\nUse Termux to open the Kali workspace.\nThis app does not read files or connect to the network.");
        details.setTextSize(18);
        details.setPadding(0, 40, 0, 40);
        layout.addView(details);
        Button test = new Button(this);
        test.setText("Run Java check");
        test.setOnClickListener(view -> details.setText("reverseCheck(0x1337) = " + reverseCheck(0x1337)));
        layout.addView(test);
        setContentView(layout);
    }
}
