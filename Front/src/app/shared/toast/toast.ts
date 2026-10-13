import { Component, inject } from '@angular/core';
import { NgClass } from '@angular/common';
import { ToastService, ToastType } from '../../core/service/toast';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [NgClass],
  template: `
    <div
      class="fixed top-4 right-4 z-[100] flex flex-col gap-3 w-[min(92vw,360px)]"
      aria-live="polite"
      aria-atomic="true"
    >
      @for (toast of toastService.toasts(); track toast.id) {
        <div
          class="flex items-start gap-3 p-4 rounded-xl border shadow-lg bg-white"
          [ngClass]="borderClass(toast.type)"
          role="alert"
        >
          <span class="material-symbols-outlined text-xl" [ngClass]="iconClass(toast.type)">
            {{ icon(toast.type) }}
          </span>
          <p class="flex-1 text-sm text-slate-700 leading-snug">{{ toast.message }}</p>
          <button
            (click)="toastService.dismiss(toast.id)"
            class="text-slate-400 hover:text-slate-600"
            aria-label="Cerrar notificación"
          >
            <span class="material-symbols-outlined text-lg">close</span>
          </button>
        </div>
      }
    </div>
  `,
})
export default class ToastComponent {
  toastService = inject(ToastService);

  icon(type: ToastType): string {
    switch (type) {
      case 'success':
        return 'check_circle';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  }

  iconClass(type: ToastType): string {
    switch (type) {
      case 'success':
        return 'text-emerald-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-blue-600';
    }
  }

  borderClass(type: ToastType): string {
    switch (type) {
      case 'success':
        return 'border-emerald-200';
      case 'error':
        return 'border-red-200';
      default:
        return 'border-blue-200';
    }
  }
}
