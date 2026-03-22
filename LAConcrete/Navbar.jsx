import React from 'react';

const Navbar = () => {
  return (
    <div className="fixed inset-x-0 top-8 z-50 flex justify-center pointer-events-none">
      <nav className="pointer-events-auto flex w-[90%] max-w-5xl items-center justify-between rounded-full border border-white/10 bg-neutral-900/80 px-6 py-3 shadow-lg backdrop-blur-md">
        <div className="text-xl font-bold tracking-tight">
          <span className="text-white">LA</span>
          <span className="text-orange-600">CONCRETE</span>
        </div>

        <div className="hidden md:flex items-center gap-8">
          <a href="index.html" className="text-sm font-medium text-gray-300 transition-colors hover:text-white">
            Home
          </a>
          <a href="services.html" className="text-sm font-medium text-gray-300 transition-colors hover:text-white">
            Services
          </a>
          <a href="projects.html" className="text-sm font-medium text-gray-300 transition-colors hover:text-white">
            Projects
          </a>
          <a href="about.html" className="text-sm font-medium text-gray-300 transition-colors hover:text-white">
            About
          </a>
        </div>

        <div>
          <a
            href="contact.html"
            className="rounded-full bg-white px-6 py-2 text-sm font-semibold text-black transition-transform hover:scale-105 hover:bg-gray-200"
          >
            Get Quote
          </a>
        </div>
      </nav>
    </div>
  );
};

export default Navbar;
