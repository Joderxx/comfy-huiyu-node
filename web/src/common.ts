export const prefixName = ""
export const varPrefixName = "ComfyMasterVar_"

export enum ParameterType {
  None= 0,
  Boolean= 1,
  Number= 2,
  String= 3,
  Image= 4,
  Range_Number= 5,
  Enum_String= 6,
  Float= 7,
  Range_Float= 8,
  Image_Mask=9,
  Switch=10,
  Switch_Group= 11,
  Enum_Int=12,
  Enum_Float=13
}

export function awaitSeconds(seconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, seconds * 1000))
}
