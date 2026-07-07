"use client";

import { ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation"

export default function CTAButton() {
    const router = useRouter();

    const handleClick = () => {
        router.push("/quiz");
    };

    return (
        <motion.button
        onClick={handleClick}
        whileHover={{
            scale: 1.05,
            boxShadow: "0px 0px 50px rgba(0,180,255,0.5)"
        }}

        whileTap={{
            scale: 0.98
        }}

        className="mt-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-4 text-lg font-semibold flex items-center gap-3"
        >
            Start Exploring
            <ArrowRight size={20}></ArrowRight>
        </motion.button>
    )
}