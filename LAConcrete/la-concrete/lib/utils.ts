<<<<<<< HEAD
import { clsx, type ClassValue } from "clsx"
=======
import { type ClassValue, clsx } from "clsx"
>>>>>>> f72fd330 (changes)
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
