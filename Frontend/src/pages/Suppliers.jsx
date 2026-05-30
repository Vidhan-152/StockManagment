import { useEffect, useState } from "react";
import FormField from "../components/FormField";
import SectionHeader from "../components/SectionHeader";
import { createSupplier, deleteSupplier, listSuppliers } from "../services/api";

const initialState = {
  name: "",
  contact_name: "",
  email: "",
  phone: "",
  avg_lead_days: "",
  reliability_score: ""
};

export default function Suppliers() {
  const [formState, setFormState] = useState(initialState);
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState({ loading: false, error: "" });

  const loadSuppliers = async () => {
    setStatus({ loading: true, error: "" });
    try {
      const data = await listSuppliers();
      setItems(data);
    } catch (error) {
      setStatus({ loading: false, error: error.message });
      return;
    }
    setStatus({ loading: false, error: "" });
  };

  useEffect(() => {
    loadSuppliers();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus({ loading: true, error: "" });

    const payload = {
      ...formState,
      avg_lead_days: Number(formState.avg_lead_days),
      reliability_score: Number(formState.reliability_score)
    };

    try {
      await createSupplier(payload);
      setFormState(initialState);
      await loadSuppliers();
    } catch (error) {
      setStatus({ loading: false, error: error.message });
      return;
    }
    setStatus({ loading: false, error: "" });
  };

  const handleDelete = async (id) => {
    setStatus({ loading: true, error: "" });
    try {
      await deleteSupplier(id);
      await loadSuppliers();
    } catch (error) {
      setStatus({ loading: false, error: error.message });
      return;
    }
    setStatus({ loading: false, error: "" });
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="glass-panel rounded-3xl p-6 shadow-xl">
        <SectionHeader title="Suppliers" subtitle="Track lead times and reliability." />
        {status.error ? (
          <div className="mt-4 rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {status.error}
          </div>
        ) : null}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-200">
            <thead className="text-xs uppercase text-slate-400">
              <tr>
                <th className="py-2">Name</th>
                <th className="py-2">Lead Days</th>
                <th className="py-2">Reliability</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody className="text-slate-100">
              {items.map((item) => (
                <tr key={item.id} className="border-t border-white/5">
                  <td className="py-3">
                    <p className="font-medium text-white">{item.name}</p>
                    <p className="text-xs text-slate-400">{item.email || "No email"}</p>
                  </td>
                  <td className="py-3">{item.avg_lead_days} days</td>
                  <td className="py-3">{item.reliability_score}</td>
                  <td className="py-3">
                    <button
                      className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-200 transition hover:border-red-400/60 hover:text-red-200"
                      onClick={() => handleDelete(item.id)}
                      type="button"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {items.length === 0 ? (
                <tr>
                  <td colSpan="4" className="py-6 text-center text-sm text-slate-400">
                    No suppliers yet. Add one using the form.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>

      <form className="glass-panel rounded-3xl p-6 shadow-xl" onSubmit={handleSubmit}>
        <SectionHeader title="Add Supplier" subtitle="Keep reliability in sync." />
        <div className="mt-5 grid gap-4">
          <FormField label="Name" name="name" value={formState.name} onChange={handleChange} />
          <FormField
            label="Contact Name"
            name="contact_name"
            value={formState.contact_name}
            onChange={handleChange}
          />
          <FormField label="Email" name="email" value={formState.email} onChange={handleChange} />
          <FormField label="Phone" name="phone" value={formState.phone} onChange={handleChange} />
          <div className="grid gap-4 md:grid-cols-2">
            <FormField
              label="Avg Lead Days"
              name="avg_lead_days"
              value={formState.avg_lead_days}
              onChange={handleChange}
            />
            <FormField
              label="Reliability Score"
              name="reliability_score"
              value={formState.reliability_score}
              onChange={handleChange}
            />
          </div>
        </div>
        <button
          className="mt-6 w-full rounded-2xl bg-amber-400/80 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-amber-300"
          type="submit"
          disabled={status.loading}
        >
          {status.loading ? "Saving..." : "Create Supplier"}
        </button>
      </form>
    </section>
  );
}
