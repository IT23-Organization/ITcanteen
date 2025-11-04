import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from "react-router"
import { routes } from '@/lib/routes'

import store, { persistor } from '@/lib/store'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
          <div className="flex min-h-svh min-w-full flex-col items-center justify-center">
            <Routes>
              {routes.map(({ path, element }) => (
                <Route key={path} path={path} element={element} />
              ))}
            </Routes>
          </div>
        </PersistGate>
      </Provider>
    </BrowserRouter>
  </StrictMode>,
)
