"use client";
import React from "react";
import { PinContainer } from "@/components/ui/3d-pin";

const cards = [
  {
    step: "01",
    title: "Preparation",
    description:
      "Site analysis and detailed excavation ensuring the perfect foundation grade.",
    image:
      "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?q=80&w=2070&auto=format&fit=crop",
    href: "/services/preparation",
  },
  {
    step: "02",
    title: "Reinforcement",
    description:
      "Precision steel fixing providing the tensile strength required for longevity.",
    image:
      "https://images.unsplash.com/photo-1621255536417-e8157778216c?q=80&w=2069&auto=format&fit=crop",
    href: "/services/reinforcement",
  },
  {
    step: "03",
    title: "Placement",
    description:
      "Expert concrete pouring and leveling ensuring a flawless architectural finish.",
    video: "/images/lavid.mp4",
    href: "/services/placement",
  },
];

export function ProcessCards() {
  return (
    <div className="w-full py-20 bg-neutral-950 flex flex-col items-center justify-center gap-20 lg:flex-row lg:flex-wrap">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="h-[25rem] w-full lg:w-[25rem] flex items-center justify-center"
        >
          <PinContainer title={card.title} href={card.href}>
            <div className="flex flex-col p-4 tracking-tight text-slate-100/50 w-[20rem] h-[20rem] bg-neutral-900/50 backdrop-blur-sm border border-white/10 rounded-2xl group">
              <div className="relative w-full h-[60%] rounded-lg overflow-hidden mb-4 border border-white/5">
                {card.video ? (
                  <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  >
                    <source src={card.video} type="video/mp4" />
                  </video>
                ) : (
                  <img
                    src={card.image}
                    alt={card.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                )}
                <div className="absolute top-2 left-2 text-4xl font-bold text-white/10 select-none">
                  {card.step}
                </div>
              </div>

              <div className="flex-1 space-y-2">
                <div className="text-xl font-bold text-slate-100">
                  {card.title}
                </div>
                <div className="text-sm text-slate-400 leading-relaxed">
                  {card.description}
                </div>
              </div>
            </div>
          </PinContainer>
        </div>
      ))}
    </div>
  );
}
