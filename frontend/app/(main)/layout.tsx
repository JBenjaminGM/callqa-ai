import { AuthGuard } from '@/components/layout/auth-guard';
import { Sidebar } from '@/components/layout/sidebar';
import { PrototypeBanner } from '@/components/layout/prototype-banner';

/** Layout de las páginas autenticadas: banner + sidebar + contenido. */
export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen flex-col">
        <PrototypeBanner />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <div className="flex flex-1 flex-col overflow-hidden">{children}</div>
        </div>
      </div>
    </AuthGuard>
  );
}
