import {checkVarName, exportPrompt, exportJson} from "./enhanced-btn"
import {ComfyExtension} from "@comfyorg/comfyui-frontend-types";

async function copy(text) {
  let clipboard = navigator.clipboard || {
    writeText: (str) => {
      return new Promise(resolve => {
        let copyInput = document.createElement('input');
        copyInput.value = str;
        document.body.appendChild(copyInput);
        copyInput.select();
        document.execCommand('copy');
        document.body.removeChild(copyInput);
        resolve();
      })
    }
  }
  if (clipboard) {
    await clipboard.writeText(text);
  }
}

const extension: ComfyExtension = {
  name: "ComfyMaster",

  commands: [
    {
      id: "copy-profile",
      label: "复制配置",
      function: async () => {
        if (!await checkVarName()) {
          return
        }
        const resp = await exportPrompt()
        await copy(resp.data)
        alert("配置复制到剪切板成功")
      }
    },
    {
      id: "export-profile",
      label: "导出配置",
      function: async () => {
        if (!await checkVarName()) {
          return
        }
        const resp = await exportPrompt()
        await exportJson(resp.name, resp.data)
      }
    }
  ],
  menuCommands: [
    {
      path: ['绘屿AI'],
      commands: ['copy-profile']
    },
    {
      path: ['绘屿AI'],
      commands: ['export-profile']
    }
  ]
}

app.registerExtension(extension)

