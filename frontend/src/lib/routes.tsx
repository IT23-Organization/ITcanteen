import Layout from '@/layout.tsx'
import Login from '@/login.tsx'
import Root from '@/root.tsx'
import History from '@/history.tsx'

import { Logs } from 'lucide-react'
import { History as HistoryIcon } from 'lucide-react'

export const routes = [
  {
    path: "/login",
    name: "Login",
    element: <Login />,
    icon: <></>
  },
  {
    path: "/",
    name: "Orders",
    element: <Layout><Root /></Layout>,
    icon: <Logs size={16} />
  },
  {
    path: "/history",
    name: "History",
    element: <Layout><History /></Layout>,
    icon: <HistoryIcon size={16} />
  }
]