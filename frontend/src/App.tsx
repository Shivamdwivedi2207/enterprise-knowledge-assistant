import AppRouter from "./routes/AppRouter";
import SourcePreviewModal from "./components/Documents/SourcePreviewModal";

function App() {
  return (
    <>
      <AppRouter />
      <SourcePreviewModal />
    </>
  );
}

export default App;