import apiService from "./api";

class CardTemplateServices {
    async getCardTemplates() {
        const response = await apiService.get("cueSearch/card-templates/");
        if (response.success) {
            return response.data
        }
        else {
            return response
        }
    }
    async addCardTemplates(payload) {
        const response = await apiService.post("cueSearch/card-templates/create/", payload);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }
    async updateCardTemplate(id, payload) {
        const response = await apiService.post("cueSearch/card-templates/update/" + id, payload);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }
    async publishCardTemplates(payload) {
        const response = await apiService.post("cueSearch/card-templates/publish/", payload);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }
    async deleteCardTemplate(id) {
        const response = await apiService.delete("cueSearch/card-templates/delete/" + id);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }



}


let cardTemplateServices = new CardTemplateServices();
export default cardTemplateServices;
