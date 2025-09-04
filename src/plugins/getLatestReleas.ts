async function getLatestRelease() {
    const res = await fetch("https://api.github.com/repos/Khubchand123/updateapp/releases/latest");
    const json = await res.json();
    return {
        tag: json.tag_name, // e.g. "v1.1"
        apkUrl: json.assets[0]?.browser_download_url
    };
}
  
export default getLatestRelease;