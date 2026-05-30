export default function FormField({ label, type = "text", name, value, onChange, placeholder }) {
  return (
    <label className="flex flex-col gap-2 text-sm text-slate-200">
      <span>{label}</span>
      <input
        className="rounded-xl border border-white/10 bg-slate-900/60 px-3 py-2 text-sm text-white shadow-sm outline-none transition focus:border-teal-400/60"
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
      />
    </label>
  );
}
