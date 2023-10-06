document.addEventListener('alpine:init', () => {
    Alpine.data('capstoneApp', () => {
        return {
            show: false,
            history: '',
            img: '',
            predictedValue: '',

            init() {
                console.log('alpine connected...')
                // this.getHistory();
                // this.get_predicted()
            },

            getHistory() {
                axios.get('/api/prediction/history/')
                    .then((result) => {
                        this.history = result.data.history;
                        console.log(result.data);
                    })
            },
            upload() {
                
                axios.post('/upload', {
                    img: this.img,
                 
                })
                .then(() => {
                    console.log('uploaded...')
                    this.getHistory();
                })
            },
            get_predicted(){
                axios.get('/predict')
                .then((result) => {
                    console.log(result.data)
                })
            },


            predict_class(img){
                
                axios.post('/predict', {
                    img: img,
                    
                })
                .then((result) => {

                    this.get_predicted()
                    // this.getHistory();
                    
                    console.log(result.data)
                })
           
                
            },
            

            deleteHistory(id) {
                axios.post('/api/prediction/delete', {
                    id: id
                })
                    .then((result) => {
                        console.log(result.data)

                        this.getHistory();

                    })
            },

        }

    })
})