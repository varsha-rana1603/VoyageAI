"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import {
    ArrowLeft,
    MapPin,
    Building2,
    ChevronDown,
    Sparkles,
    CheckCircle2,
    AlertTriangle,
} from "lucide-react";

interface StaysResultsPageProps {
    recommendations: any[];
    destination: any;
    error: string | null;
    onBack: () => void;
}

type SortKey = "match" | "price" | "distance";

// --- Data normalization helpers ---
// The backend already computes a precise ranking_breakdown.overall score;
// match_percentage is just a coarse bucket ("<75%"), so prefer the real number when available.
function getMatchScore(stay: any): number {
    if (typeof stay?.ranking_breakdown?.overall === "number") {
        return stay.ranking_breakdown.overall;
    }
    if (typeof stay.match_percentage === "string") {
        const num = parseFloat(stay.match_percentage.replace(/[^\d.]/g, ""));
        return Number.isNaN(num) ? 0 : num;
    }
    return 0;
}

const PRICE_ORDER: Record<string, number> = { low: 1, medium: 2, high: 3, luxury: 4 };

function priceTier(priceLevel: string | number | undefined): number {
    if (typeof priceLevel === "number") return Math.min(4, Math.max(1, priceLevel));
    if (typeof priceLevel === "string") return PRICE_ORDER[priceLevel.toLowerCase()] ?? 2;
    return 2;
}

function formatPriceLabel(priceLevel: string | undefined): string {
    if (!priceLevel) return "Not specified";
    return priceLevel.charAt(0).toUpperCase() + priceLevel.slice(1) + " budget";
}

// Cleans up messy geocoded addresses like "Name, Road, -, State, India"
function formatAddress(address: string | undefined): string {
    if (!address) return "Address not available";
    return address
        .split(",")
        .map((part) => part.trim())
        .filter((part) => part.length > 0 && part !== "-")
        .join(", ");
}

function confidenceStyle(confidence: string | undefined): { dot: string; text: string } {
    const c = (confidence ?? "").toLowerCase();
    if (c.includes("excellent") || c.includes("great")) {
        return { dot: "bg-green-400", text: "text-green-300" };
    }
    if (c.includes("worth")) {
        return { dot: "bg-amber-400", text: "text-amber-300" };
    }
    if (c.includes("not") || c.includes("poor")) {
        return { dot: "bg-red-400", text: "text-red-300" };
    }
    return { dot: "bg-cyan-400", text: "text-cyan-300" };
}

function MatchRing({ score }: { score: number }) {
    const radius = 22;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;

    return (
        <div className="relative flex h-14 w-14 flex-shrink-0 items-center justify-center">
            <svg width="56" height="56" viewBox="0 0 56 56" className="-rotate-90">
                <circle cx="28" cy="28" r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="5" />
                <motion.circle
                    cx="28"
                    cy="28"
                    r={radius}
                    fill="none"
                    stroke="url(#stayScoreGradient)"
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset: offset }}
                    transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
                />
                <defs>
                    <linearGradient id="stayScoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#22d3ee" />
                        <stop offset="100%" stopColor="#a855f7" />
                    </linearGradient>
                </defs>
            </svg>
            <span className="absolute text-[11px] font-bold text-white">{Math.round(score)}%</span>
        </div>
    );
}

function PriceTier({ level }: { level: number }) {
    return (
        <div className="flex items-center gap-0.5">
            {[1, 2, 3, 4].map((tier) => (
                <span key={tier} className={`text-sm font-semibold ${tier <= level ? "text-cyan-400" : "text-white/15"}`}>
                    ₹
                </span>
            ))}
        </div>
    );
}

function BreakdownBar({ label, value }: { label: string; value: number }) {
    return (
        <div>
            <div className="mb-1 flex justify-between text-xs text-zinc-400">
                <span className="capitalize">{label}</span>
                <span>{Math.round(value)}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-white/10">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, value)}%` }}
                    transition={{ duration: 0.8 }}
                    className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"
                />
            </div>
        </div>
    );
}

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
    { key: "match", label: "Best Match" },
    { key: "price", label: "Price" },
    { key: "distance", label: "Distance" },
];

export default function StaysResultsPage({
    recommendations,
    destination,
    error,
    onBack,
}: StaysResultsPageProps) {
    const [sortKey, setSortKey] = useState<SortKey>("match");
    const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
    const reduceMotion = useReducedMotion();

    const toggleExpanded = (id: string) => {
        setExpandedIds((prev) => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const sortedStays = useMemo(() => {
        const copy = [...recommendations];
        copy.sort((a, b) => {
            if (sortKey === "match") return getMatchScore(b) - getMatchScore(a);
            if (sortKey === "price") return priceTier(a.price_level) - priceTier(b.price_level);
            return (a.distance_from_center ?? 0) - (b.distance_from_center ?? 0);
        });
        return copy;
    }, [recommendations, sortKey]);

    return (
        <main className="min-h-screen bg-[#05060b] px-6 py-10 text-white">
            <div className="mx-auto max-w-7xl">
                <button
                    onClick={onBack}
                    className="mb-8 flex items-center gap-2 text-sm text-zinc-400 transition hover:text-cyan-400"
                >
                    <ArrowLeft size={16} />
                    Back to destinations
                </button>

                <motion.div
                    initial={reduceMotion ? undefined : { opacity: 0, y: 20 }}
                    animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="flex flex-col justify-between gap-6 border-b border-white/10 pb-8 sm:flex-row sm:items-end"
                >
                    <div>
                        <div className="flex items-center gap-2 text-cyan-400">
                            <Building2 size={16} />
                            <span className="text-sm uppercase tracking-[0.2em]">Stays</span>
                        </div>
                        <h1 className="mt-2 text-4xl font-bold sm:text-5xl">
                            Where to stay in {destination?.name}
                        </h1>
                        <p className="mt-3 text-zinc-400">
                            {sortedStays.length} stay{sortedStays.length !== 1 ? "s" : ""} matched to your trip
                        </p>
                    </div>

                    <div className="flex flex-shrink-0 gap-2">
                        {SORT_OPTIONS.map((option) => (
                            <button
                                key={option.key}
                                onClick={() => setSortKey(option.key)}
                                className={`rounded-full border px-4 py-2 text-sm font-medium transition ${sortKey === option.key
                                        ? "border-cyan-400/40 bg-cyan-500/15 text-cyan-300"
                                        : "border-white/10 bg-white/5 text-zinc-400 hover:border-white/20 hover:text-white"
                                    }`}
                            >
                                {option.label}
                            </button>
                        ))}
                    </div>
                </motion.div>

                {error && (
                    <div className="mt-10 rounded-2xl border border-red-500/20 bg-red-500/10 p-6 text-red-300">
                        {error}
                    </div>
                )}

                {!error && sortedStays.length === 0 && (
                    <div className="mt-10 rounded-2xl border border-white/10 bg-white/5 p-10 text-center text-zinc-400">
                        <p className="text-lg text-white">No stays found yet</p>
                        <p className="mt-2 text-sm">
                            Try a different destination, or check back once more stays are added.
                        </p>
                    </div>
                )}

                {!error && sortedStays.length > 0 && (
                    <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        <AnimatePresence mode="popLayout">
                            {sortedStays.map((stay, i) => {
                                const isExpanded = expandedIds.has(stay.id);
                                const score = getMatchScore(stay);
                                const confStyle = confidenceStyle(stay.confidence);

                                return (
                                    <motion.div
                                        key={stay.id}
                                        layout
                                        initial={reduceMotion ? undefined : { opacity: 0, y: 24 }}
                                        animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
                                        exit={reduceMotion ? undefined : { opacity: 0, y: -12 }}
                                        transition={{ duration: 0.4, delay: reduceMotion ? 0 : i * 0.05 }}
                                        className="flex flex-col self-start rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl transition-colors hover:border-cyan-500/30"
                                    >
                                        <div className="flex flex-col p-6">
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="min-w-0">
                                                    <div className="flex items-center gap-2 text-xs text-zinc-500">
                                                        <span className={`h-1.5 w-1.5 rounded-full ${confStyle.dot}`} />
                                                        <span className={confStyle.text}>{stay.confidence ?? "Match"}</span>
                                                    </div>
                                                    <h2 className="mt-1 truncate text-lg font-semibold leading-snug">
                                                        {stay.name}
                                                    </h2>
                                                </div>
                                                <MatchRing score={score} />
                                            </div>

                                            <div className="mt-3 flex items-start gap-2 text-sm text-zinc-400">
                                                <MapPin size={14} className="mt-0.5 flex-shrink-0" />
                                                <span className="line-clamp-2">{formatAddress(stay.address)}</span>
                                            </div>

                                            {stay.reasons?.[0] && (
                                                <p className="mt-3 text-sm text-zinc-300">{stay.reasons[0]}</p>
                                            )}

                                            <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-4 text-sm">
                                                <PriceTier level={priceTier(stay.price_level)} />
                                                <span className="text-zinc-400">{stay.distance_from_center} km away from city center</span>
                                            </div>

                                            <button
                                                onClick={() => toggleExpanded(stay.id)}
                                                className="mt-4 flex items-center justify-center gap-1.5 text-sm text-cyan-400 transition hover:text-cyan-300"
                                            >
                                                {isExpanded ? "Hide details" : "Why this stay"}
                                                <motion.span
                                                    animate={{ rotate: isExpanded ? 180 : 0 }}
                                                    transition={{ duration: 0.2 }}
                                                >
                                                    <ChevronDown size={14} />
                                                </motion.span>
                                            </button>
                                        </div>

                                        <AnimatePresence initial={false}>
                                            {isExpanded && (
                                                <motion.div
                                                    initial={{ height: 0, opacity: 0 }}
                                                    animate={{ height: "auto", opacity: 1 }}
                                                    exit={{ height: 0, opacity: 0 }}
                                                    transition={{ duration: 0.3, ease: "easeInOut" }}
                                                    className="overflow-hidden"
                                                >
                                                    <div className="space-y-5 border-t border-white/10 px-6 pb-6 pt-5">
                                                        {stay.pros?.length > 0 && (
                                                            <div className="space-y-2">
                                                                {stay.pros.map((pro: string) => (
                                                                    <div key={pro} className="flex items-start gap-2 text-sm text-zinc-300">
                                                                        <CheckCircle2 size={15} className="mt-0.5 flex-shrink-0 text-green-400" />
                                                                        {pro}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}

                                                        {stay.cons?.length > 0 && (
                                                            <div className="space-y-2">
                                                                {stay.cons.map((con: string) => (
                                                                    <div key={con} className="flex items-start gap-2 text-sm text-zinc-400">
                                                                        <AlertTriangle size={15} className="mt-0.5 flex-shrink-0 text-amber-400" />
                                                                        {con}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}

                                                        {stay.ranking_breakdown && (
                                                            <div>
                                                                <div className="mb-3 flex items-center gap-1.5 text-xs uppercase tracking-wider text-zinc-500">
                                                                    <Sparkles size={12} />
                                                                    Match breakdown
                                                                </div>
                                                                <div className="space-y-3">
                                                                    {Object.entries(stay.ranking_breakdown)
                                                                        .filter(([key, value]) =>
                                                                            key !== "overall" && Number(value) > 0
                                                                        )
                                                                        .map(([key, value]) => (
                                                                            <BreakdownBar
                                                                                key={key}
                                                                                label={key}
                                                                                value={value as number}
                                                                            />
                                                                        ))}
                                                                </div>
                                                            </div>
                                                        )}

                                                        <p className="text-xs text-zinc-400">
                                                            {formatPriceLabel(stay.price_level)}
                                                        </p>
                                                    </div>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </motion.div>
                                );
                            })}
                        </AnimatePresence>
                    </div>
                )}
            </div>
        </main>
    );
}