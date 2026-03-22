import { ProcessCards } from "@/components/process-cards";

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      <div className="container mx-auto px-4 py-20">
        <h2 className="text-4xl md:text-6xl font-bold text-center mb-10 text-white">
          Our Process
        </h2>

        {/* The 3D Cards Section */}
        <ProcessCards />
      </div>
    </main>
  );
}
