import {computed, ComputedRef, type Ref, ref, watch} from 'vue';
import {createEmptyTemplate} from '@/utils/factoriesProtocolo.ts';
import type {Protocolo, TemplateCiclo} from "@/types/typesProtocolo.ts";

export function useProtocoloModelos(protocolo: Ref<Partial<Protocolo>>) {
  const activeTemplateIndex = ref(0);

  const templates: ComputedRef<TemplateCiclo[]> = computed((): TemplateCiclo[] => {
    if (!protocolo.value.templatesCiclo) {
      protocolo.value.templatesCiclo = [];
    }
    return protocolo.value.templatesCiclo;
  });

  const currentTemplate = computed(() => {
    if (templates.value.length === 0) return null;
    return templates.value[activeTemplateIndex.value];
  });

  const getUniqueName = (baseName: string, isCopy = false, excludeIndex = -1) => {
    const existingNames = templates.value
      .filter((_, idx) => idx !== excludeIndex)
      .map((t) => t.idTemplate);

    let candidate = baseName;
    if (isCopy && existingNames.includes(candidate)) {
      candidate = `${baseName} (Cópia)`;
    }

    let counter = 1;
    const baseForCounter = isCopy ? `${baseName} (Cópia` : baseName.replace(/\s\d+$/, '');

    while (existingNames.includes(candidate)) {
      if (isCopy) {
        counter++;
        candidate = `${baseName} (Cópia ${counter})`;
      } else {
        candidate = `${baseForCounter} ${counter}`;
        counter++;
      }
    }
    return candidate;
  };

  const handleNameBlur = () => {
    if (!currentTemplate.value) return;
    const currentName = currentTemplate.value.idTemplate || 'Sem Nome';
    const uniqueName = getUniqueName(currentName, false, activeTemplateIndex.value);
    if (uniqueName !== currentName) {
      currentTemplate.value.idTemplate = uniqueName;
    }
  };

  const addTemplate = () => {
    const newName = getUniqueName('Variante', false);
    templates.value.push(createEmptyTemplate(newName));
    activeTemplateIndex.value = templates.value.length - 1;
  };

  const duplicateTemplate = () => {
    if (!currentTemplate.value) return;
    const original = currentTemplate.value;
    const newName = getUniqueName(original.idTemplate, true);
    const clone = JSON.parse(JSON.stringify(original));
    clone.idTemplate = newName;
    templates.value.push(clone);
    activeTemplateIndex.value = templates.value.length - 1;
  };

  const removeTemplate = () => {
    if (templates.value.length <= 1) return;
    templates.value.splice(activeTemplateIndex.value, 1);
  };

  watch(() => templates.value.length, (newLen) => {
    if (activeTemplateIndex.value >= newLen) {
      activeTemplateIndex.value = Math.max(0, newLen - 1);
    }
  });

  return {
    activeTemplateIndex,
    currentTemplate,
    templates,
    addTemplate,
    duplicateTemplate,
    removeTemplate,
    handleNameBlur
  };
}
