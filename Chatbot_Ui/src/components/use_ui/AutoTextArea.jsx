import { useState, useRef, useEffect } from "react"
import { InputGroupTextarea } from "../ui/input-group" // your component

export default function SmartTextarea() {
  const [value, setValue] = useState("")
  const textareaRef = useRef(null)
  const MAX_HEIGHT = 200 // pixels

  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = "auto"
    const newHeight = Math.min(textarea.scrollHeight, MAX_HEIGHT)
    textarea.style.height = `${newHeight}px`
    textarea.style.overflowY =
      textarea.scrollHeight > MAX_HEIGHT ? "auto" : "hidden"
  }, [value])

  return (
    <InputGroupTextarea
      ref={textareaRef}
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder="Ask, Search or Chat..."
      className="resize-none text-2xl bg-muted/50 border rounded-2xl p-3 focus-visible:ring-0 focus-visible:outline-none min-h-[52px]"
    />
  )
}