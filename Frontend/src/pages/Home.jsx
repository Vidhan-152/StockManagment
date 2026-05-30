import SectionHeader from "../components/SectionHeader";

export default function Home() {
  return (
    <section className="glass-panel rounded-3xl px-6 py-8 shadow-xl">
      <SectionHeader
        title="Quick Test Console"
        subtitle="Use the tabs to create, list, and delete records while you build out the backend."
      />
      <div className="mt-6 grid gap-4 text-sm text-slate-200 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="font-semibold text-white">Products</p>
          <p className="mt-2 text-slate-300">
            Add inventory items, update stock, and verify alerts logic without leaving the browser.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="font-semibold text-white">Suppliers</p>
          <p className="mt-2 text-slate-300">
            Track lead times and reliability scores so the alert system stays accurate.
          </p>
        </div>
      </div>
      <div className="mt-6 rounded-2xl border border-dashed border-white/20 bg-white/5 p-4 text-sm text-slate-300">
        <p>API base URL is read from VITE_API_BASE_URL (defaults to http://localhost:8000).</p>
      </div>
    </section>
  );
}
