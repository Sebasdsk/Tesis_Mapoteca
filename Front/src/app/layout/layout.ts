import { Component, inject, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../core/service/auth';

interface NavItem {
  icon: string;
  label: string;
  route: string;
  adminOnly: boolean;
}

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './layout.html',
  styleUrl: './layout.css',
})
export default class LayoutComponent {
  private authService = inject(AuthService);

  sidebarOpen = signal(false);
  currentUser = this.authService.currentUser;
  isAdmin = this.authService.isAdmin;

  navItems: NavItem[] = [
    { icon: 'auto_stories', label: 'Catálogo', route: '/catalogo', adminOnly: false },
    { icon: 'swap_horiz', label: 'Préstamos', route: '/prestamos', adminOnly: false },
    { icon: 'group', label: 'Usuarios', route: '/usuarios', adminOnly: true },
    { icon: 'bar_chart', label: 'Reportes', route: '/reportes', adminOnly: true },
  ];

  toggleSidebar() {
    this.sidebarOpen.update((v) => !v);
  }

  closeSidebar() {
    this.sidebarOpen.set(false);
  }

  logout() {
    this.authService.logout();
  }
}
