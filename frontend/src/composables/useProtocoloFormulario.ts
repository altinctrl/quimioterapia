import {computed, ref} from 'vue';
import {useRouter} from 'vue-router';
import {toast} from 'vue-sonner';
import {useAppStore} from '@/stores/storeGeral.ts';
import {createEmptyProtocolo} from '@/utils/factoriesProtocolo.ts';
import type {Protocolo} from "@/types/typesProtocolo.ts";

export function useProtocoloFormulario(protocoloId?: string) {
  const router = useRouter();
  const appStore = useAppStore();

  const loading = ref(false);
  const formData = ref<Partial<Protocolo>>(createEmptyProtocolo());

  const isEditMode = computed(() => !!protocoloId);

  const initForm = async () => {
    try {
      loading.value = true;
      if (appStore.protocolos.length === 0) {
        await appStore.fetchProtocolos();
      }

      if (isEditMode.value) {
        const encontrado = appStore.getProtocoloById(protocoloId!);

        if (encontrado) {
          const clone = JSON.parse(JSON.stringify(encontrado));
          if (!clone.templatesCiclo || clone.templatesCiclo.length === 0) {
            clone.templatesCiclo = createEmptyProtocolo();
          }

          formData.value = clone;
        } else {
          toast.error("Protocolo não encontrado");
          await router.push({name: 'Ajustes', query: {tab: 'protocolos'}});
        }
      }
    } catch (error) {
      console.error(error);
      toast.error("Erro ao carregar dados do protocolo");
    } finally {
      loading.value = false;
    }
  };

  const cleanDataForSave = (data: Partial<Protocolo>) => {
    const payload = JSON.parse(JSON.stringify(data));

    if (!payload.fase || payload.fase === '' || payload.fase === 'none') {
      payload.fase = null;
    }

    if (payload.templatesCiclo) {
      payload.templatesCiclo.forEach((template: any) => {
        if (template.blocos) {
          template.blocos.forEach((bloco: any) => {
            if (bloco.itens) {
              bloco.itens = bloco.itens.map((item: any) => {
                if (item.tipo === 'medicamento_unico') {
                  const {labelGrupo, opcoes, ...rest} = item;
                  return rest;
                } else if (item.tipo === 'grupo_alternativas') {
                  const {dados, ...rest} = item;
                  return rest;
                }
                return item;
              });
            }
          });
        }
      });
    }
    return payload;
  };

  const saveProtocolo = async () => {
    try {
      const payload = cleanDataForSave(formData.value);

      if (isEditMode.value) {
        await appStore.atualizarProtocolo(protocoloId!, payload);
        toast.success('Protocolo atualizado com sucesso');
      } else {
        await appStore.adicionarProtocolo(payload);
        toast.success('Protocolo criado com sucesso');
      }

      await router.push({name: 'Ajustes', query: {tab: 'protocolos'}});
    } catch (error) {
      console.error(error);
      toast.error('Erro ao salvar protocolo');
    }
  };

  const excluirProtocolo = async () => {
    if (!protocoloId) return;
    if (!confirm('Tem certeza que deseja excluir este protocolo? Esta ação não pode ser desfeita.')) return;

    try {
      loading.value = true;
      await appStore.excluirProtocolo(protocoloId);
      toast.success('Protocolo removido com sucesso');
      await router.push({name: 'Ajustes', query: {tab: 'protocolos'}});
    } catch (error) {
      console.error(error);
      toast.error('Erro ao remover protocolo');
    } finally {
      loading.value = false;
    }
  };

  const cancelEdit = () => {
    void router.push({name: 'Ajustes', query: {tab: 'protocolos'}});
  };

  return {
    formData,
    loading,
    isEditMode,
    initForm,
    saveProtocolo,
    excluirProtocolo,
    cancelEdit
  };
}
