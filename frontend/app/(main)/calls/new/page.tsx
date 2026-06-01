'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { UploadCloud, FileAudio, X } from 'lucide-react';
import { api, getErrorMessage } from '@/lib/api';
import { useAgents } from '@/lib/queries';
import { useAuthStore } from '@/lib/auth';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Spinner, ErrorState } from '@/components/ui/feedback';

const ALLOWED = ['.mp3', '.wav', '.m4a', '.ogg', '.flac'];
const MAX_MB = 100;
const MAX_FILES = 20;

/**
 * Subida de un grupo de llamadas.
 *
 * El supervisor solo elige los audios, la campaña, un comentario opcional y
 * el responsable. La IA detectará el nombre del ejecutivo de cada llamada.
 */
export default function NewCallPage() {
  const router = useRouter();
  const { data: agents } = useAgents();
  const user = useAuthStore((s) => s.user);

  const [files, setFiles] = useState<File[]>([]);
  const [campaign, setCampaign] = useState('');
  const [comment, setComment] = useState('');
  const [responsible, setResponsible] = useState(user?.name ?? '');
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Campañas existentes (para sugerencias del campo campaña).
  const campaigns = Array.from(
    new Set((agents ?? []).map((a) => a.campaign).filter(Boolean)),
  ) as string[];

  function validateFile(f: File): string | null {
    const ext = '.' + (f.name.split('.').pop() ?? '').toLowerCase();
    if (!ALLOWED.includes(ext)) return `"${f.name}": formato no soportado.`;
    if (f.size > MAX_MB * 1024 * 1024)
      return `"${f.name}": supera los ${MAX_MB} MB.`;
    return null;
  }

  function onFilesChange(e: React.ChangeEvent<HTMLInputElement>) {
    setError(null);
    const selected = Array.from(e.target.files ?? []);
    for (const f of selected) {
      const err = validateFile(f);
      if (err) {
        setError(err);
        return;
      }
    }
    // Acumula con los ya seleccionados, sin pasar del máximo.
    const combined = [...files, ...selected].slice(0, MAX_FILES);
    setFiles(combined);
    e.target.value = '';
  }

  function removeFile(index: number) {
    setFiles((fs) => fs.filter((_, i) => i !== index));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (files.length === 0) {
      setError('Selecciona al menos un archivo de audio.');
      return;
    }

    const form = new FormData();
    files.forEach((f) => form.append('audios', f));
    if (campaign) form.append('campaign', campaign);
    if (comment) form.append('comment', comment);
    if (responsible) form.append('responsible', responsible);

    setUploading(true);
    setProgress(0);
    try {
      await api.post('/calls/batch', form, {
        onUploadProgress: (evt) => {
          if (evt.total) {
            setProgress(Math.round((evt.loaded / evt.total) * 100));
          }
        },
      });
      // Tras subir el lote, se va al listado a ver el procesamiento.
      router.push('/calls');
    } catch (err) {
      setError(getErrorMessage(err));
      setUploading(false);
    }
  }

  return (
    <>
      <Header title="Subir grupo de llamadas" />
      <main className="flex-1 overflow-y-auto p-6">
        <form onSubmit={onSubmit} className="mx-auto max-w-2xl">
          <Card className="flex flex-col gap-5">
            <div>
              <CardTitle>Nuevo lote de llamadas</CardTitle>
              <p className="mt-1 text-small text-text-secondary">
                Sube los audios MP3. La IA identificará automáticamente al
                ejecutivo de cada llamada a partir de la transcripción.
              </p>
            </div>

            {/* Selector de archivos */}
            <div>
              <Label>Archivos de audio (hasta {MAX_FILES})</Label>
              <label
                className="flex cursor-pointer flex-col items-center justify-center
                           gap-2 rounded-xl border-2 border-dashed border-border
                           bg-bg-secondary px-4 py-8 text-center transition-colors
                           hover:border-accent-primary"
              >
                <UploadCloud size={32} className="text-text-muted" />
                <span className="text-body text-text-secondary">
                  Haz clic para seleccionar uno o varios archivos
                </span>
                <span className="text-small text-text-muted">
                  {ALLOWED.join(', ')} — máx. {MAX_MB} MB por archivo
                </span>
                <input
                  type="file"
                  accept={ALLOWED.join(',')}
                  multiple
                  className="hidden"
                  onChange={onFilesChange}
                  disabled={uploading}
                />
              </label>

              {/* Lista de archivos seleccionados */}
              {files.length > 0 && (
                <ul className="mt-3 flex flex-col gap-2">
                  {files.map((f, i) => (
                    <li
                      key={`${f.name}-${i}`}
                      className="flex items-center gap-2 rounded-lg border
                                 border-border bg-bg-secondary px-3 py-2"
                    >
                      <FileAudio size={16} className="text-accent-primary" />
                      <span className="flex-1 truncate text-small text-text-primary">
                        {f.name}
                      </span>
                      <span className="text-small text-text-muted">
                        {(f.size / 1024 / 1024).toFixed(1)} MB
                      </span>
                      {!uploading && (
                        <button
                          type="button"
                          onClick={() => removeFile(i)}
                          aria-label="Quitar archivo"
                          className="text-text-muted hover:text-danger"
                        >
                          <X size={16} />
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Campaña */}
            <div>
              <Label htmlFor="campaign">Campaña</Label>
              <Input
                id="campaign"
                list="campaign-options"
                placeholder="Ej. Tarjetas Premium"
                value={campaign}
                onChange={(e) => setCampaign(e.target.value)}
                disabled={uploading}
              />
              <datalist id="campaign-options">
                {campaigns.map((c) => (
                  <option key={c} value={c} />
                ))}
              </datalist>
            </div>

            {/* Comentario opcional */}
            <div>
              <Label htmlFor="comment">Comentario (opcional)</Label>
              <Textarea
                id="comment"
                rows={3}
                placeholder="Notas sobre este lote de llamadas…"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                disabled={uploading}
              />
            </div>

            {/* Responsable */}
            <div>
              <Label htmlFor="responsible">Responsable de la subida</Label>
              <Input
                id="responsible"
                value={responsible}
                onChange={(e) => setResponsible(e.target.value)}
                disabled={uploading}
              />
            </div>

            {error && <ErrorState message={error} />}

            {uploading && (
              <div>
                <div className="mb-1 flex justify-between text-small text-text-secondary">
                  <span>Subiendo {files.length} archivo(s)…</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-bg-accent">
                  <div
                    className="h-full bg-accent-primary transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.push('/calls')}
                disabled={uploading}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={uploading}>
                {uploading ? <Spinner /> : <UploadCloud size={18} />}
                Subir y procesar
              </Button>
            </div>
          </Card>
        </form>
      </main>
    </>
  );
}
