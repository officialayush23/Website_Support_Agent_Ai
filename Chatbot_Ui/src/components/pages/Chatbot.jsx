import React, { useEffect, useRef, useState } from 'react'

import { ArrowUp, Plus } from "lucide-react"  // ✅ fixed icon names
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu"
import {
    InputGroup,
    InputGroupAddon,
    InputGroupButton,
    InputGroupInput,
    InputGroupText,
} from "@/components/ui/input-group"
import { Separator } from "@/components/ui/separator"
import ThemeProvider from '../use_ui/theme-provider'
import ModeToggle from '../use_ui/ModeToggle'
import SmartTextarea from '../use_ui/AutoTextArea'
import { InputGroupTextarea } from '../ui/input-group'

function Chatbot() {
    const [value, setValue] = useState("")
    const textareaRef = useRef(null)
    const MAX_HEIGHT = 200

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
        <section className="relative h-screen w-full transition-all duration-300 flex flex-col">
            <div className="absolute top-4 right-4">
                <ModeToggle />
            </div>
            {/* Chat messages area */}
            <div className="flex-1 transition-all duration-300 overflow-y-auto p-4">
                {/* You can map messages here */}
                <p className="text-gray-400 text-5xl text-center mt-10">Daksha.ai</p>
            </div>

            {/* Fixed input section */}
            <div className="sticky transition-all duration-300 bottom-0 w-full border-t  border-gray-700 p-2">
                <InputGroup className='rounded-3xl'>
                    <InputGroupTextarea placeholder="Ask, Search or Chat..." 

                        ref={textareaRef}
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        className="resize-none text-2xl transition-all duration-300  p-3 focus-visible:ring-0 focus-visible:outline-none min-h-[52px]" />
                    <InputGroupAddon align="inline-end">
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <InputGroupButton
                                    variant="outline"
                                    className="rounded-full"
                                    size="icon-md"
                                >
                                    <Plus />

                                </InputGroupButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                side="top"
                                align="center"
                                className="[--radius:0.95rem] transition-all duration-300"
                            >
                                <DropdownMenuItem>Auto</DropdownMenuItem>
                                <DropdownMenuItem>Agent</DropdownMenuItem>
                                <DropdownMenuItem>Manual</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>


                        <Separator orientation="vertical" className="!h-4" />

                        <InputGroupButton
                            variant="default"
                            className="rounded-full ml-auto transition-all duration-300"
                            size="icon-md"
                        >
                            <ArrowUp />
                            <span className="sr-only">Send</span>
                        </InputGroupButton>
                    </InputGroupAddon>
                </InputGroup>
            </div>
        </section>
    )
}

export default Chatbot
