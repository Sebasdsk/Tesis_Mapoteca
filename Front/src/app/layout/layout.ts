import { Component, inject, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../core/service/auth';
import ToastComponent from '../shared/toast/toast';

interface NavItem {
  icon: string;
  label: string;
  route: string;
  adminOnly: boolean;
  managerOnly?: boolean;
  disabled?: boolean;
}

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ToastComponent],
  templateUrl: './layout.html',
  styleUrl: './layout.css',
})
export default class LayoutComponent {
  private authService = inject(AuthService);

  sidebarOpen = signal(false);
  currentUser = this.authService.currentUser;
  isAdmin = this.authService.isAdmin;
  canManageCatalog = this.authService.canManageCatalog;

  navItems: NavItem[] = [
    { icon: 'auto_stories', label: 'Catálogo', route: '/catalogo', adminOnly: false },
    { icon: 'swap_horiz', label: 'Préstamos', route: '/prestamos', adminOnly: false },
    { icon: 'language', label: 'Fuentes INEGI', route: '/fuentes-inegi', adminOnly: false, managerOnly: true },
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
