import {ParameterType,  prefixName, varPrefixName} from "./common";

export async function checkVarName() {
  const p = await window.app.graphToPrompt()

  let findOutput = false
  for (let node of Object.values(p.output)) {
    if (!node["class_type"].startsWith(`${prefixName}CMaster_Output`) && !node["class_type"].startsWith(`${prefixName}CMaster_Input`)) {
      continue
    }

    if (node["class_type"].startsWith(`${prefixName}CMaster_Output`)) {
      findOutput = true
    }
    const varName = node.inputs["var_name"]
    if (!varName || typeof varName !== "string" || varName.trim() === "") {
      alert(`${node["class_type"]} 没有变量名`)
      return false
    }
  }

  if (!findOutput) {
    alert("没有找到：输出节点")
    return false
  }
  return true
}

function getGroup(id, workflow, outputs) {
  const node = workflow.nodes.find(e => e.id === parseInt(id))
  if (!node) {
    return []
  }

  const ret = []

  if (node.type === `${prefixName}CMaster_InputSwitchNode` || node.type === `${prefixName}CMaster_InputSwitchGroupNode`) {
    const n = outputs[id]["inputs"]["open_data"]
    if (n) {
      ret.push(`single-${n[0]}`)
    }
  }

  for (let group of workflow.groups) {
    const [posX, posY] = node.pos
    const [x, y, width, height] = group.bounding
    if (posX >= x && posX <= x + width && posY >= y && posY <= y + height) {
      ret.push(`group-${group.title}`)
    }
  }
  ret.push(`single-${id}`)
  return ret
}

export async function exportPrompt() {
  const p = await window.app.graphToPrompt()

  const workflow = {...p.output}
  let metadataNode: any
  let metadataNodeKey: any
  let os: "Windows" | "Macos" | "Linux" = "Windows"
  for (let [key, value] of Object.entries(workflow)) {
    if (value.class_type === `${prefixName}CMaster_InputImage` || value["class_type"] === `${prefixName}CMaster_InputMaskImageNode`) {
      value.inputs["image"] = ""
    } else if (value.class_type === `${prefixName}LoadImageToBase64`) {
      delete workflow[key]
    } else if (value.class_type === `${prefixName}WorkflowMetadataConfig`) {
      metadataNode = value
      metadataNodeKey = key
      os = value.inputs["os"]
    } else if (value.class_type === `${prefixName}CTool_ImageMaskTestNode`) {
      value.class_type = `${prefixName}CTool_ImageMaskNode`
      value.inputs = {}
    } else if (value.class_type === `${prefixName}CTool_ImageWorkflowMetadataTestNode`) {
      value.class_type = `${prefixName}CTool_ImageWorkflowMetadataNode`
      value.inputs = {}
    }
    if (value._meta) {
      //@ts-ignore
      value._meta.group = getGroup(key, p.workflow, p.output)
    }
  }

  if (metadataNodeKey) {
    delete workflow[metadataNodeKey]
  }

  let modelType = ["其他", "SD1.5", "SDXL", "FLUX"].indexOf(metadataNode?.inputs?.modelType || "")
  if (modelType === -1) {
    modelType = 0
  }
  let type = ["默认", "局部重绘", "放大", "局部修复"].indexOf(metadataNode?.inputs?.type || "")
  if (type === -1) {
    type = 0
  }
  const params: any[] = Object.values(workflow).filter(e => e.class_type.startsWith(`${prefixName}CMaster_Input`)).map(e => parseInput(e, os))
  const outputs: any[] = Object.values(workflow).filter(e => e.class_type.startsWith(`${prefixName}CMaster_Output`)).map(e => parseOutput(e))

  const saveObj = {
    code: metadataNode?.inputs?.code || "",
    name: metadataNode?.inputs?.name || "",
    description: metadataNode?.inputs?.description || "",
    type: type,
    modelType: modelType,
    groupInfo: metadataNode?.inputs?.groupInfo || "",
    maxWidth: metadataNode?.inputs?.maxWidth || 2048,
    maxHeight: metadataNode?.inputs?.maxHeight || 2048,
    workflow: workflow,
    params,
    outputs
  }
  return {
    name: metadataNode?.inputs?.name || "",
    data: JSON.stringify(saveObj, null, 2)
  }
}



const algorithms = ["", "固定值", "随机值", "递增", "递减"]

function parseInput(node: any, os: "Windows" | "Macos" | "Linux") {
  const type = node.class_type
  const varName = node.inputs["var_name"]
  const newVarName = `${varPrefixName}${varName}`;
  const description = node.inputs["description"] || varName
  const isExport = node.inputs["export"]
  const order = node.inputs["order"]
  const placeholder = node.inputs["placeholder"] || ""
  const group = (node["_meta"] || {})["group"] || []
  const defaultGenerateAlgorithm = Math.max(0, algorithms.indexOf(node.inputs["default_generate_algorithm"]))

  let ret: any = {
    key: newVarName,
    name: description,
    type: ParameterType.Image,
    isExport: isExport,
    order: order || 0,
    defaultGenerateAlgorithm,
    group,
    placeholder
  };

  if (type === `${prefixName}CMaster_InputImage`) {
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Image,
      isExport: isExport,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputString`) {
    const text = node.inputs["text"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.String,
      isExport: isExport,
      stringDefaultValue: text,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputEnumString`) {
    const text = node.inputs["text"]
    const enums = node.inputs["enums"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_String,
      isExport: isExport,
      stringDefaultValue: text,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputBoolean`) {
    const num = node.inputs["value"]
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Boolean,
      isExport: isExport,
      boolDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputInt`) {
    const num = node.inputs["number"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Number,
      isExport: isExport,
      numberDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputRangeInt`) {
    const num = node.inputs["number"]
    const min = node.inputs["min"]
    const max = node.inputs["max"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Range_Number,
      isExport: isExport,
      numberDefaultValue: num,
      minNumberValue: min,
      maxNumberValue: max,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputEnumInt`) {
    const num = node.inputs["number"]
    const enums = node.inputs["enums"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_Int,
      isExport: isExport,
      numberDefaultValue: num,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputFloat`) {
    const num = node.inputs["number"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Float,
      isExport: isExport,
      floatDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputRangeFloat`) {
    const num = node.inputs["number"]
    const min = node.inputs["min"]
    const max = node.inputs["max"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Range_Float,
      isExport: isExport,
      floatDefaultValue: num,
      minFloatValue: min,
      maxFloatValue: max,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputEnumFloat`) {
    const num = node.inputs["number"]
    const enums = node.inputs["enums"]

    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_Float,
      isExport: isExport,
      numberDefaultValue: num,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputCheckpoint`) {
    const text = node.inputs["ckpt_name"]
    const enums: string = (node.inputs["checkpoints"] || "").split("\n").map(e => e.trim()).map(e => {
        if (os === "Windows") {
          e = e.replace(/\//g, "\\")
        } else {
          e = e.replace(/\\/g, "/")
        }
        return e
      }).join("\n")
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_String,
      isExport: isExport,
      stringDefaultValue: text,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputLoraNode`) {
    const text = node.inputs["lora_name"]
    const enums: string = (node.inputs["loras"] || "").split("\n").map(e => e.trim()).map(e => {
        if (os === "Windows") {
          e = e.replace(/\//g, "\\")
        } else {
          e = e.replace(/\\/g, "/")
        }
        return e
      }).join("\n")
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_String,
      isExport: isExport,
      stringDefaultValue: text,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputMaskImageNode`) {
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Image_Mask,
      isExport: isExport,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputSwitchNode`) {
    const num = node.inputs["value"]
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Switch,
      isExport: isExport,
      boolDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  } else if (type === `${prefixName}CMaster_InputSwitchGroupNode`) {
    const num = node.inputs["value"]
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Switch_Group,
      isExport: isExport,
      boolDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    }
  }

  return ret;
}

const OutputType = {
  None: 0,
  String: 1,
  Image: 2,
  Video: 3,
  Audio: 4,
}

function parseOutput(node) {
  const type = node.class_type
  const varName = node.inputs["var_name"]
  const newVarName = `${varPrefixName}${varName}`;
  const description = node.inputs["description"] || varName
  const isExport = node.inputs["export"]
  const order = node.inputs["order"]
  let ret = {
    key: newVarName,
    name: description,
    type: OutputType.None,
    isExport: isExport,
    order: order || 0
  }

  if (type === `${prefixName}CMaster_OutputImage`) {
    ret.type = OutputType.Image;
  }
  return ret;
}

async function getFilename(defaultName: string) {

  if (await window.app.api.getSetting('Comfy.PromptFilename')) {
    defaultName = prompt('保存为:', defaultName)
    if (!defaultName) return
    if (!defaultName.toLowerCase().endsWith('.json')) {
      defaultName += '.json'
    }
  }
  return defaultName
}

export async function exportJson(name: string, json: string) {
  const blob = new Blob([json], {type: 'application/json'})

  const file = await getFilename(`${name}.json`)
  if (!file) return
  window.comfyAPI.utils.downloadBlob(file, blob)
}