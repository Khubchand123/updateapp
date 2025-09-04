package com.example.updateapp;

import android.os.Bundle;
import android.util.Log;
import com.getcapacitor.BridgeActivity;
import com.example.updateapp.plugin.ApkUpdaterPlugin;

public class MainActivity extends BridgeActivity {
    private static final String TAG = "MainActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.d(TAG, "onCreate: Starting MainActivity");

        // Explicitly register the plugin BEFORE super.onCreate in Capacitor 4
        Log.d(TAG, "onCreate: Manually registering ApkUpdaterPlugin");
        registerPlugin(ApkUpdaterPlugin.class);
        Log.d(TAG, "onCreate: Plugin registration complete");

        super.onCreate(savedInstanceState);
    }
}