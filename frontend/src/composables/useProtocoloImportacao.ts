import {ref} from 'vue'
import {toast} from 'vue-sonner'
import {Bloco, Protocolo, TemplateCiclo} from "@/types/typesProtocolo.ts";

export function useProtocoloImportacao() {
  const isProcessing = ref(false)
  const ignored = ref(0)

  const validarProtocolo = (p: any): Partial<Protocolo> | null => {
    if (!p.nome || typeof p.duracaoCicloDias !== 'number') return null;
    if (!Array.isArray(p.templatesCiclo)) return null;

    const templatesValidos = p.templatesCiclo
      .map((template: TemplateCiclo): TemplateCiclo | null => {
        if (!template.idTemplate || !Array.isArray(template.blocos)) return null;
        const blocosComItens = template.blocos.filter((bloco: Bloco) =>
          Array.isArray(bloco.itens) && bloco.itens.length > 0
        );
        return blocosComItens.length > 0
          ? {...template, blocos: blocosComItens}
          : null;
      })
      .filter((t: TemplateCiclo | null): t is TemplateCiclo => t !== null);
    if (templatesValidos.length === 0) return null;
    return {
      ...p,
      templatesCiclo: templatesValidos
    };
  }

  const handleFileUpload = async (event: Event): Promise<any[] | null> => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return null;

    isProcessing.value = true;
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const content = JSON.parse(e.target?.result as string);
          const listaBruta = Array.isArray(content) ? content : [content];

          const listaLimpa = listaBruta
            .map(validarProtocolo)
            .filter((p): p is Protocolo => p !== null);

          if (listaLimpa.length === 0) {
            toast.error("Nenhum protocolo válido encontrado.");
            resolve(null);
          } else {
            ignored.value = listaBruta.length - listaLimpa.length;
            resolve(listaLimpa);
          }
        } catch (err) {
          toast.error("Erro ao ler arquivo JSON.");
          resolve(null);
        } finally {
          isProcessing.value = false;
          target.value = '';
        }
      };
      reader.readAsText(file);
    });
  }

  return {handleFileUpload, isProcessing, ignored};
}
