import React from "react";
import { FlippingCard } from "@/components/ui/flipping-card";

// --- Types ---
interface CardData {
  id: string;
  front: {
    imageSrc: string;
    imageAlt: string;
    title: string;
    description: string;
  };
  back: {
    description: string;
    buttonText: string;
  };
}

// --- Data: Mapped from your previous Gallery ---
const cardsData: CardData[] = [
  // ROW 1: SITE PREP
  {
    id: "excavation",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1590059590038-a28a2a89c89e?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Excavation",
      title: "Excavation",
      description: "Deep soil removal and site clearing.",
    },
    back: {
      description:
        "We handle heavy-duty excavation to remove unstable soil, ensuring a rock-solid foundation for your pour.",
      buttonText: "Request Prep",
    },
  },
  {
    id: "leveling",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Laser Leveling",
      title: "Laser Leveling",
      description: "Precision grading for perfect flatness.",
    },
    back: {
      description:
        "Using advanced laser technology, we grade the substrate to millimeter accuracy before a single drop of concrete is poured.",
      buttonText: "Learn More",
    },
  },
  {
    id: "compaction",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Compaction",
      title: "Compaction",
      description: "Solid base work prevents cracking.",
    },
    back: {
      description:
        "High-vibration compaction ensures the sub-base is dense and stable, preventing future settling or structural cracks.",
      buttonText: "Details",
    },
  },

  // ROW 2: STEEL FIXING
  {
    id: "rebar",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1535732759880-bbd5c7265e3f?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Rebar Grid",
      title: "Rebar Grid",
      description: "Tensile strength reinforcement.",
    },
    back: {
      description:
        "We install custom steel rebar grids to provide the tensile strength required for heavy loads and industrial use.",
      buttonText: "Specs",
    },
  },
  {
    id: "mesh",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Mesh Install",
      title: "Mesh Install",
      description: "Crack control and stability.",
    },
    back: {
      description:
        "Steel mesh is laid precisely to bind the concrete slab together, significantly reducing thermal cracking.",
      buttonText: "View Options",
    },
  },
  {
    id: "structural",
    front: {
      imageSrc:
        "https://plus.unsplash.com/premium_photo-1661962360699-0f04e8d38865?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Structural",
      title: "Structural Walls",
      description: "Commercial grade vertical pours.",
    },
    back: {
      description:
        "Formwork and reinforcement for retaining walls, columns, and vertical architectural elements.",
      buttonText: "Get Quote",
    },
  },

  // ROW 3: THE POUR
  {
    id: "pumping",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1621252179027-94459d27d3ee?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Pumping",
      title: "Concrete Pumping",
      description: "Boom pump delivery systems.",
    },
    back: {
      description:
        "We utilize boom pumps to deliver concrete to hard-to-reach areas efficiently and without mess.",
      buttonText: "Capabilities",
    },
  },
  {
    id: "finishing",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1617104551722-3b2d51366400?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Finishing",
      title: "Power Floating",
      description: "Smooth, hard-wearing surfaces.",
    },
    back: {
      description:
        "Mechanical power floating creates a dense, smooth surface ideal for warehouses, garages, and industrial floors.",
      buttonText: "Finishes",
    },
  },
  {
    id: "polished",
    front: {
      imageSrc:
        "https://images.unsplash.com/photo-1626296185858-a58399e52516?auto=format&fit=crop&q=80&w=800",
      imageAlt: "Polished",
      title: "Polished Concrete",
      description: "High-end interior aesthetic.",
    },
    back: {
      description:
        "We grind and polish the surface to expose the aggregate, creating a stunning, durable floor for modern interiors.",
      buttonText: "Gallery",
    },
  },
];

// --- Internal Components (Front/Back Faces) ---

interface GenericCardFrontProps {
  data: CardData["front"];
}

function GenericCardFront({ data }: GenericCardFrontProps) {
  return (
    <div className="flex flex-col h-full w-full bg-neutral-900 rounded-lg overflow-hidden border border-neutral-800">
      <div className="h-3/5 w-full overflow-hidden">
        <img
          src={data.imageSrc}
          alt={data.imageAlt}
          className="w-full h-full object-cover transition-transform duration-500 hover:scale-110"
        />
      </div>
      <div className="p-4 flex flex-col justify-center h-2/5">
        <h3 className="text-xl font-black uppercase font-sans text-white">
          {data.title}
        </h3>
        <p className="text-sm mt-2 text-neutral-400">{data.description}</p>
      </div>
    </div>
  );
}

interface GenericCardBackProps {
  data: CardData["back"];
}

function GenericCardBack({ data }: GenericCardBackProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full p-6 bg-neutral-900 rounded-lg border border-[#FF4D00]">
      <p className="text-sm leading-relaxed text-gray-300 text-center">
        {data.description}
      </p>
      <button className="mt-6 bg-[#FF4D00] hover:bg-white hover:text-black transition-colors text-white font-bold uppercase tracking-wider px-6 py-2 rounded-full text-xs">
        {data.buttonText}
      </button>
    </div>
  );
}

// --- Main Page Export ---

export default function ServicesPage() {
  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-[#FF4D00] selection:text-white">
      {/* Simple Nav Simulation */}
      <nav className="fixed top-0 w-full z-50 p-6 flex justify-center">
        <div className="bg-neutral-900/80 backdrop-blur-md px-8 py-3 rounded-full border border-white/10 flex items-center gap-8">
          <span className="font-bold text-xl">
            LA <span className="text-[#FF4D00]">CONCRETE</span>
          </span>
          <div className="hidden md:flex gap-6 text-sm text-gray-300">
            <a href="/" className="hover:text-white transition-colors">
              Home
            </a>
            <a href="#" className="text-white">
              Services
            </a>
          </div>
          <button className="bg-white text-black px-4 py-1.5 rounded-full text-sm font-bold hover:bg-gray-200 transition-colors">
            Get Quote
          </button>
        </div>
      </nav>

      <main className="pt-32 pb-20 px-4 md:px-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-20 space-y-4">
          <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tight">
            Our <span className="text-[#FF4D00]">Services</span>
          </h1>
          <p className="text-neutral-400 max-w-2xl mx-auto">
            From deep excavation to the final polished finish. Hover over a card
            to reveal details.
          </p>
        </div>

        {/* Grid of Flipping Cards */}
        <div className="flex gap-6 flex-wrap justify-center">
          {cardsData.map((card) => (
            <FlippingCard
              key={card.id}
              width={320}
              height={380}
              frontContent={<GenericCardFront data={card.front} />}
              backContent={<GenericCardBack data={card.back} />}
              className="bg-transparent border-0" // Resetting default styles to let inner content handle it
            />
          ))}
        </div>
      </main>
    </div>
  );
}
