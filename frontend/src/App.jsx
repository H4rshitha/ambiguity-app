import { BrowserRouter, Routes, Route } from "react-router-dom";
import Analyzer from "./pages/Analyzer";
import History from "./pages/History";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Analyzer />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
