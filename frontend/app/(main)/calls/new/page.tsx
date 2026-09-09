'use client';

import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { UploadCloud, FileAudio, FolderOpen, X } from 'lucide-react';
import { api, getErrorMessage } from '@/lib/api';
import { useCampaignList } from '@/lib/queries';
import { useAuthStore } from '@/lib/auth';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Spinner, ErrorState } from '@/components/ui/feedback';
import { cn } from '@/lib/utils';

const ALLOWED = ['.mp3', '.wav', '.m4a', '.ogg', '.flac'];
const MAX_MB = 100;
const MAX_FILES = 20;

/** True si el nombre acaba en una de las extensiones de audio admitidas. */
function esAudio(name: string): boolean {
  return ALLOWED.includes('.' + (name.split('.').pop() ?? '').toLowerCase());
}

/**
 * Recorre una carpeta soltada y devuelve los audios que contiene, a cualquier
 * profundidad.
 *
 * Al arrastrar una carpeta el navegador no entrega archivos, sino una entrada
 * de directorio que hay que recorrer a mano. `readEntries` además devuelve los
 * hijos por tandas, no todos de golpe: hay que seguir llamándolo hasta que
 * conteste vacío, o una carpeta con muchas grabaciones llegaría cortada.
 */
async function leerCarpeta(entry: FileSystemEntry, out: File[]): Promise<void> {
  if (out.length >= MAX_FILES) return;

  if (entry.isFile) {
    const file = await new Promise<File>((resolve, reject) =>
      (entry as FileSystemFileEntry).file(resolve, reject),
    );
    if (esAudio(file.name)) out.push(file);
    return;
  }

  if (entry.isDirectory) {
    const reader = (entry as FileSystemDirectoryEntry).createReader();
    for (;;) {
      const lote = await new Promise<FileSystemEntry[]>((resolve, reject) =>
        reader.readEntries(resolve, reject),
      );
      if (lote.length === 0) break;
      for (const hijo of lote) {
        await leerCarpeta(hijo, out);
      }
    }
  }
}

/**
 * Subida de un grupo de llamadas.
 *
 * El supervisor solo elige los audios, la campaña, un comentario opcional y
 * el responsable. La IA detectará el nombre del ejecutivo de cada llamada.
 */
export default function NewCallPage() {
  const router = useRouter();
  const { data: campaigns } = useCampaignList({ active: true });
  const user = useAuthStore((s) => s.user);

  const [files, setFiles] = useState<File[]>([]);
  const [campaignId, setCampaignId] = useState('');
  const [comment, setComment] = useState('');
  const [responsible, setResponsible] = useState(user?.name ?? '');
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [scanning, setScanning] = useState(false);
  const folderInputRef = useRef<HTMLInputElement>(null);

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

  /**
   * Añade archivos ya obtenidos (de una carpeta o del selector), avisando si
   * alguno no vale o si el lote se queda corto por el máximo.
   */
  function addFiles(nuevos: File[]) {
    if (nuevos.length === 0) {
      setError('La carpeta no contiene ningún audio en un formato admitido.');
      return;
    }
    for (const f of nuevos) {
      const err = validateFile(f);
      if (err) {
        setError(err);
        return;
      }
    }
    const combinados = [...files, ...nuevos];
    setFiles(combinados.slice(0, MAX_FILES));
    setError(
      combinados.length > MAX_FILES
        ? `Se han añadido los primeros ${MAX_FILES} audios; el resto se ha descartado.`
        : null,
    );
  }

  /** Audios seleccionados con el botón «elegir carpeta» (input webkitdirectory). */
  function onFolderChange(e: React.ChangeEvent<HTMLInputElement>) {
    setError(null);
    addFiles(Array.from(e.target.files ?? []).filter((f) => esAudio(f.name)));
    e.target.value = '';
  }

  /** Carpeta (o archivos) soltados sobre la zona de subida. */
  async function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    if (uploading) return;
    setError(null);

    const items = Array.from(e.dataTransfer.items)
      .map((i) => i.webkitGetAsEntry?.())
      .filter((entry): entry is FileSystemEntry => Boolean(entry));

    // Navegador sin API de directorios: al menos los archivos sueltos entran.
    if (items.length === 0) {
      addFiles(Array.from(e.dataTransfer.files).filter((f) => esAudio(f.name)));
      return;
    }

    setScanning(true);
    try {
      const encontrados: File[] = [];
      for (const entry of items) {
        await leerCarpeta(entry, encontrados);
      }
      addFiles(encontrados);
    } catch {
      setError('No se pudo leer la carpeta. Prueba a seleccionar los archivos.');
    } finally {
      setScanning(false);
    }
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
    if (campaignId) form.append('campaign_id', campaignId);
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
                onDragOver={(e) => {
                  e.preventDefault();
                  if (!uploading) setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
                className={cn(
                  `flex cursor-pointer flex-col items-center justify-center gap-2
                   rounded-card border-2 border-dashed bg-bg-secondary px-4 py-8
                   text-center transition-colors`,
                  dragging
                    ? 'border-accent-primary bg-bg-accent'
                    : 'border-border hover:border-accent-primary',
                )}
              >
                {scanning ? (
                  <Spinner className="h-8 w-8 text-accent-primary" />
                ) : (
                  <UploadCloud size={32} className="text-text-muted" />
                )}
                <span className="text-body text-text-secondary">
                  {scanning
                    ? 'Buscando audios en la carpeta…'
                    : 'Arrastra aquí una carpeta entera, o haz clic para elegir archivos'}
                </span>
                <span className="text-small text-text-muted">
                  {ALLOWED.join(', ')} — máx. {MAX_MB} MB por archivo, {MAX_FILES}{' '}
                  por lote
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

              {/* Salida para navegadores sin arrastre de carpetas, y para quien
                  prefiera el diálogo del sistema. */}
              <div className="mt-2 flex flex-wrap items-center gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => folderInputRef.current?.click()}
                  disabled={uploading || scanning}
                >
                  <FolderOpen size={16} />
                  Elegir una carpeta
                </Button>
                {files.length > 0 && (
                  <span className="text-small text-text-muted">
                    {files.length} de {MAX_FILES} seleccionados
                  </span>
                )}
              </div>
              <input
                ref={folderInputRef}
                type="file"
                multiple
                className="hidden"
                onChange={onFolderChange}
                disabled={uploading}
                // `webkitdirectory` no está en los tipos de React pero lo
                // entienden todos los navegadores de escritorio.
                {...({ webkitdirectory: '' } as Record<string, string>)}
              />

              {/* Lista de archivos seleccionados */}
              {files.length > 0 && (
                <ul className="mt-3 flex flex-col gap-2">
                  {files.map((f, i) => (
                    <li
                      key={`${f.name}-${i}`}
                      className="flex items-center gap-2 rounded-control border
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
              <Select
                id="campaign"
                value={campaignId}
                onChange={(e) => setCampaignId(e.target.value)}
                disabled={uploading}
              >
                <option value="">Sin campaña</option>
                {(campaigns ?? []).map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </Select>
              <p className="mt-1 text-small text-text-muted">
                La IA evaluará la oferta de cada llamada contra la nota de
                producto de la campaña.{' '}
                <Link
                  href="/campaigns/new"
                  className="text-accent-primary hover:underline"
                >
                  Crear campaña
                </Link>
              </p>
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
