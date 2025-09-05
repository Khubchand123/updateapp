// import React, { useEffect, useState } from "react";
import ApkUpdater from "./plugins/ApkUpdater";
// import getCurrentVersion from "./plugins/getCurrentVersion";
import getLatestRelease from "./plugins/getLatestReleas";

import './App.css'
function App() {
  const updateApp = async () => {
    // We need the APK url, so fetch the full latest release object
    const latest = await getLatestRelease();
    if (!latest.apkUrl) {
      console.error("No APK URL found in latest release.");
      return;
    }
    console.log("Updating from URL:", latest.apkUrl);
    await ApkUpdater.updateApp({
      url: latest.apkUrl,
    });
  };
  return (
    <div className="App">
      <button
          onClick={async () => {
            await updateApp();
          }}
        >
          Update APK
        </button>
    </div>
  );
}

export default App;
