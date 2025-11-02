import React, { useContext } from "react";
import { LightbulbIcon, Moon, MoonIcon, Settings2Icon, Sun } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "../use_ui/theme-provider"; // adjust path if needed

function ModeToggle({ className = "" }) {
  const { setTheme } = useTheme();
 
  return (
    <DropdownMenu>
      <DropdownMenuTrigger className={className} asChild>
        <Button variant="outline" size="icon" className="relative">
          <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}><LightbulbIcon/> Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}><MoonIcon/> Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}><Settings2Icon/> System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default ModeToggle;
