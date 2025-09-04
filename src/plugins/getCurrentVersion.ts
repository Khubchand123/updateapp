import { App } from '@capacitor/app';

async function getCurrentVersion() {
  const info = await App.getInfo();
  console.log("Current version:", info.version, "Code:", info.build);
  return info;
}


export default getCurrentVersion;
