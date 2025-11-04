import {
  Sidebar as UiSidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar"

import { routes } from '@/lib/routes'

export function Sidebar({ ...props }: React.ComponentProps<typeof UiSidebar>) {
  return (
    <UiSidebar collapsible="offcanvas" {...props}>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Orders</SidebarGroupLabel>
          <SidebarGroupContent>
            {routes.map(({ path, name }) => (
              <SidebarMenuItem key={path}>
                <SidebarMenuButton asChild>
                  <a href={path}>{name}</a>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </UiSidebar>
  )
}