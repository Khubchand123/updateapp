package com.example.updateapp.plugin;

import android.content.Intent;
import android.net.Uri;
import android.os.AsyncTask;
import android.util.Log;
import androidx.core.content.FileProvider;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.PluginMethod;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

@CapacitorPlugin(name = "ApkUpdater")
public class ApkUpdaterPlugin extends Plugin {

    @PluginMethod
    public void updateApp(PluginCall call) {
        String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("URL is required");
            return;
        }
        new DownloadAndInstall(getContext(), call).execute(url);
    }

    private static class DownloadAndInstall extends AsyncTask<String, Void, File> {
        private final PluginCall call;
        private final android.content.Context context;

        DownloadAndInstall(android.content.Context context, PluginCall call) {
            this.context = context;
            this.call = call;
        }

        @Override
        protected File doInBackground(String... urls) {
            String fileUrl = urls[0];
            File apkFile = null;
            try {
                URL url = new URL(fileUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.connect();

                apkFile = new File(context.getExternalCacheDir(), "update.apk");
                FileOutputStream fos = new FileOutputStream(apkFile);
                BufferedInputStream bis = new BufferedInputStream(conn.getInputStream());

                byte[] buffer = new byte[1024];
                int count;
                while ((count = bis.read(buffer)) != -1) {
                    fos.write(buffer, 0, count);
                }

                fos.close();
                bis.close();
            } catch (Exception e) {
                Log.e("ApkUpdater", "Download failed", e);
            }
            return apkFile;
        }

        @Override
        protected void onPostExecute(File apkFile) {
            if (apkFile != null && apkFile.exists()) {
                Uri apkUri = FileProvider.getUriForFile(
                        context,
                        context.getPackageName() + ".provider",
                        apkFile
                );

                Intent intent = new Intent(Intent.ACTION_VIEW);
                intent.setDataAndType(apkUri, "application/vnd.android.package-archive");
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_GRANT_READ_URI_PERMISSION);
                context.startActivity(intent);

                call.resolve();
            } else {
                call.reject("Download failed");
            }
        }
    }
}
