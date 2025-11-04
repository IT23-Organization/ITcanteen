import { routes } from '@/lib/routes'
import { useSelector, useDispatch } from 'react-redux'
import { clearUser } from '@/lib/slices/user'
import { useNavigate } from 'react-router'

import { Button } from './components/ui/button'
import { Toaster } from "@/components/ui/sonner"

export default function Layout({ children }: { children: React.ReactNode }) {
  const filteredRoutes = routes.filter(route => route.path !== '/login');
  const isActive = (path: string) => {
    return window.location.pathname === path;
  }

  const navigation = useNavigate();
  const dispatch = useDispatch();
  const user = useSelector((state: any) => state.user);

  const logout = () => {
    dispatch(clearUser());
    navigation('/login');
  }

  return (
    <div className="flex-grow min-w-full flex flex-row bg-neutral-100">
      <div className="w-64 bg-neutral-100 p-4 flex flex-col">
        <h1 className="mt-4 py-4 px-4 font-bold text-blue-500 text-lg">Dashboard</h1>
        <div className="flex-grow">
          {filteredRoutes.map((route) => (
            <a
              key={route.path}
              href={route.path}
              className={`
                py-1 px-4 rounded hover:bg-neutral-200 mb-2 text-gray-700
                transition-colors duration-200
                flex flex-row items-center gap-2
                ${isActive(route.path)
                  ? 'bg-neutral-900 text-neutral-50 hover:bg-neutral-700'
                  : ''}
              `}
            >
              {route.icon} {route.name}
            </a>
          ))}
        </div>
        <div>
          <Button onClick={logout}>Logout</Button>
        </div>
      </div>
      <main className="flex-grow m-4 justify-start px-8 bg-neutral-50 rounded-xl border-1 border-neutral-200">
        {children}
      </main>
      <Toaster />
    </div>
  )
}