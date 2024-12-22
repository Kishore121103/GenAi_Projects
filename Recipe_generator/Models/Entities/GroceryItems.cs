namespace Recipe_generator.Models.Entities
{
    public class GroceryItem
    {
        public Guid GroceryItemId { get; set; } = Guid.NewGuid();
        public Guid SessionId { get; set; }
        public string ItemName { get; set; }
        public string Quantity { get; set; }
        public DateTime PurchaseDate { get; set; }
        public DateTime CreatedAt { get; set; }
    }

}
