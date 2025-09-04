package com.example.updateapp;

import android.os.Bundle;
import android.util.Log;
import com.getcapacitor.BridgeActivity;
import com.example.updateapp.plugin.ApkUpdaterPlugin;
//import android.content.pm.PackageInfo;
//import android.content.pm.PackageManager;
//import android.widget.Toast;
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

//    @Override
//    protected void onStart() {
//        super.onStart();
//
//        try {
//            PackageInfo pInfo = getPackageManager().getPackageInfo(getPackageName(), 0);
//            String versionName = pInfo.versionName;
//            int versionCode = pInfo.versionCode;
//            Toast.makeText(this, "Current Version: " + versionName + " (" + versionCode + ")", Toast.LENGTH_LONG).show();
//        } catch (PackageManager.NameNotFoundException e) {
//            e.printStackTrace();
//        }
//    }
}