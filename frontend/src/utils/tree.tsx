import Icon from "~/components/CustomIcons/Icon"
import ThreeDotsLoader from "~/components/CustomIcons/ThreeDotsLoader"

export interface TreeItem {
  id: string
  title: string
  icon?: React.ReactElement
  status?: React.ReactElement | string
  children?: TreeItem[]
}

export interface TreeItemData<T> extends Omit<TreeItem, "children"> {
  children?: TreeItemData<T>[]
  data: T
}

export interface ListItem {
  id: string
  number?: string
  title?: string
  dmetadata?: Record<string, any>
  icon?: string
  data?: string
}

export interface ActionItem {
  id: string
  parent_id?: string
  data?: string
  icon?: string
  dmetadata?: Record<string, any>
  loading?: boolean
}

export function buildSectionTree(list: ListItem[], expanded: boolean = false): TreeItemData<ListItem>[] {
  const nodes = new Map<string, TreeItemData<ListItem>>()
  const roots: TreeItemData<ListItem>[] = []
  
  list.forEach((item) => {
    const newNode = {
      id: item.id,
      title: expanded ? `${item.number} ${item.title}` : item.number!,
      status: item.dmetadata?.page ? `${item.dmetadata.page}` : undefined,
      data: item,
    }
    
    nodes.set(item.number!, newNode)
    
    if (!item.number!.includes(".")) {
      roots.push(newNode)
      return
    }
    
    const parentNumber = item.number!.substring(0, item.number!.lastIndexOf("."))
    const parentNode = nodes.get(parentNumber)
    
    if (parentNode) {
      if (!parentNode.children) parentNode.children = []
      parentNode.children.push(newNode)
    } else {
      roots.push(newNode)
    }
  })
  
  return roots
}

const supportedIcons = {
  TbWriting: Icon.TbWriting,
  AiOutlineFileSearch: Icon.AiOutlineFileSearch,
  TfiWrite: Icon.TfiWrite,
  TbSection: Icon.TbSection,
  BiErrorAlt: Icon.BiErrorAlt,
  SiWritedotas: Icon.SiWritedotas,
  MdOutlineQuickreply: Icon.MdOutlineQuickreply,
  RiDraftLine: Icon.RiDraftLine,
  BiCheck: Icon.BiCheck,
  AiOutlineStop: Icon.AiOutlineStop,
  GrDocumentStore: Icon.GrDocumentStore,
}

export function buildActionTree(list: ActionItem[]): TreeItemData<ActionItem>[] {
  const nodes = new Map<string, TreeItemData<ActionItem>>()
  const roots: TreeItemData<ActionItem>[] = []
  
  list.forEach((item) => {
    const icon = item.icon || "BiQuestionMark"
    const IconComponent = supportedIcons[icon as keyof typeof supportedIcons] || Icon.BiErrorAlt
    
    let status = <Icon.BiCheck />
    if (item.loading) {
      status = <ThreeDotsLoader />
    } else if (item.dmetadata?.result) {
      status = item.dmetadata.result
    } else if (item.dmetadata?.cancelled) {
      status = <Icon.AiOutlineStop />
    }
    
    const newNode = {
      id: item.id,
      title: item.data || "Unknown action",
      icon: <IconComponent />,
      status,
      data: item,
    } as TreeItemData<ActionItem>
    
    nodes.set(item.id, newNode)
    
    if (!item.parent_id) {
      roots.push(newNode)
    } else {
      const parentNode = nodes.get(item.parent_id)
      if (parentNode) {
        if (!parentNode.children) parentNode.children = []
        parentNode.children.push(newNode)
      } else {
        roots.push(newNode)
      }
    }
  })
  
  return roots
}
