import { NavLink } from "react-router-dom";

const navLinkClasses = ({ isActive }) =>
  `px-3 py-1.5 rounded-full text-sm transition ${
    isActive
      ? "bg-teal-400/20 text-teal-200"
      : "text-slate-300 hover:text-white hover:bg-white/10"
  }`;

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen">
      <header className="px-6 py-6">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4">
          <div>
            <p className="section-title text-2xl text-white">Stock Managment</p>
            <p className="text-sm text-slate-300">
              Minimal console for Products and Suppliers CRUD
            </p>
          </div>
          <nav className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 p-1">
            <NavLink to="/" className={navLinkClasses}>
              Overview
            </NavLink>
            <NavLink to="/products" className={navLinkClasses}>
              Products
            </NavLink>
            <NavLink to="/suppliers" className={navLinkClasses}>
              Suppliers
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="px-6 pb-12">
        <div className="mx-auto max-w-6xl fade-in">{children}</div>
      </main>
    </div>
  );
}
