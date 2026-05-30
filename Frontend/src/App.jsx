import { Route, Routes } from "react-router-dom";
import AppShell from "./layouts/AppShell";
import Home from "./pages/Home";
import Products from "./pages/Products";
import Suppliers from "./pages/Suppliers";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/suppliers" element={<Suppliers />} />
      </Routes>
    </AppShell>
  );
}
