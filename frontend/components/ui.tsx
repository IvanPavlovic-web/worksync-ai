"use client";

import { forwardRef, type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/cn";

export const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement>>(({ className, ...props }, ref) => <button ref={ref} className={cn("ui-button", className)} {...props} />);
Button.displayName = "Button";
export const Card = ({ className, children }: { className?: string; children: ReactNode }) => <section className={cn("ui-card", className)}>{children}</section>;
export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => <input ref={ref} className={cn("ui-input", className)} {...props} />);
Input.displayName = "Input";
export const Badge = ({ children, className }: { children: ReactNode; className?: string }) => <span className={cn("ui-badge", className)}>{children}</span>;
export const EmptyState = ({ title, children }: { title: string; children?: ReactNode }) => <div className="ui-empty"><h2>{title}</h2>{children}</div>;

