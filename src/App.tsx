import React, { useEffect } from "react";
import ApkUpdater from "./plugins/ApkUpdater";



import './App.css'
function App() {
  useEffect(() => {
    const checkUpdate = async () => {
      try {
        await ApkUpdater.updateApp({
          url: "https://gsf-fl.softonic.com/42a/f7d/449256ee4c7ea8b530ccb6434527fb4648/com-jetstartgames-chess-82-67665060-a6640849bb820a969b38576cef1dd85a.apk?Expires=1757011426&Signature=e657e24cd52f0779d96659b7e5d10162ff17a4dd&url=https://chess-i7d.en.softonic.com/android&Filename=com-jetstartgames-chess-82-67665060-a6640849bb820a969b38576cef1dd85a.apk",
        });
        console.log("Update triggered");
      } catch (err) {
        console.error("Update failed", err);
      }
    };

    checkUpdate();
  }, []);

  return (
    <div className="App">
      <h2>APK Update Demo</h2>
      <button
        onClick={async () => {
          await ApkUpdater.updateApp({
            url: "https://gsf-fl.softonic.com/42a/f7d/449256ee4c7ea8b530ccb6434527fb4648/com-jetstartgames-chess-82-67665060-a6640849bb820a969b38576cef1dd85a.apk?Expires=1757011426&Signature=e657e24cd52f0779d96659b7e5d10162ff17a4dd&url=https://chess-i7d.en.softonic.com/android&Filename=com-jetstartgames-chess-82-67665060-a6640849bb820a969b38576cef1dd85a.apk",
          });
        }}
      >
        Update APK
      </button>
    </div>
  );
}

export default App;
