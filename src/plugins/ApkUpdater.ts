import { registerPlugin } from '@capacitor/core';

export interface ApkUpdaterPlugin {
  updateApp(options: { url: string }): Promise<void>;
}

// Register the plugin
const ApkUpdater = registerPlugin<ApkUpdaterPlugin>('ApkUpdater');

export default ApkUpdater;
