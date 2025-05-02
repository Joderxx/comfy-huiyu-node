import {checkVarName, exportPrompt, exportJson} from "./enhanced-btn.js"

const htmlStyleElement = document.createElement("style");
htmlStyleElement.innerHTML = `

`

document.head.appendChild(htmlStyleElement);

const htmlDivElement = document.createElement("div");
htmlDivElement.className = "comfyui-button-group"

let boxElement = document.querySelector("body > div.comfyui-body-top > div > div.comfyui-menu-right > div");
if (!boxElement) {
  boxElement = document.querySelector("#comfyui-body-top > div.comfyui-menu.flex.items-center > div.comfyui-menu-right.flex-shrink-0 > div")
}
boxElement.appendChild(htmlDivElement);

const exportBtn = document.createElement("button");
exportBtn.className = "comfyui-button";
exportBtn.innerHTML = "导出CM配置";
exportBtn.onclick = async () => {
  if (!await checkVarName()) {
    return false
  }
  const resp = await exportPrompt()
  exportJson(resp.name, resp.data)
}

htmlDivElement.appendChild(exportBtn);
