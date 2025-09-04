import React, { useEffect, useState } from "react";
import ApkUpdater from "./plugins/ApkUpdater";
import getCurrentVersion from "./plugins/getCurrentVersion";
import getLatestRelease from "./plugins/getLatestReleas";

import './App.css'
function App() {
  const [cVersion, setCVersion] = useState('');
  const [lVersion, setLVersion] = useState('');
  const getCVersion = async () => {
    const current = await getCurrentVersion();
    console.log(current.version);
    const normalized = (current.version || "").trim();
    setCVersion(normalized);
    return normalized;
  };
  const getLVersion = async () => {
    const latest = await getLatestRelease();
    const normalized = latest.tag.replace(/^v/, "").trim();
    console.log(normalized);
    setLVersion(normalized);
    return normalized;
  };
  useEffect(() => {
    // Fetch current and latest versions once on mount
    (async () => {
      await getCVersion();
      await getLVersion();
    })();
  }, []);
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
  const checkNewVersion = async () => {
    const latest = await getLatestRelease();
    const normalized = latest.tag.replace(/^v/, "").trim();
    if (normalized == lVersion) {
      alert("You are using the latest version");
    } else {
      alert("New version available");
    }
    console.log(normalized);
    setLVersion(normalized);
    return normalized;
  };
  return (
    <div className="App">
      <h2>APK Update Demo</h2>
      <h3>Current Version: {cVersion}</h3>
      {cVersion != lVersion && <h3>Latest Version: {lVersion}</h3>}
      {(cVersion && lVersion && cVersion !== lVersion) && (
        <button
          onClick={async () => {
            await updateApp();
          }}
        >
          Update APK {lVersion}
        </button>
      )}
      {(cVersion && lVersion && cVersion == lVersion) && (
        <button
          onClick={async () => {
            await checkNewVersion();
          }}
        >
          Check New Version
        </button>
      )}
    </div>
  );
}

export default App;
