using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;

namespace Recipe_generator.Models.Entities
{
    public class session
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public Guid SessionId { get; set; }  // Unique identifier for the session

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;  // When the session was created

        public DateTime LastUpdatedAt { get; set; } = DateTime.UtcNow;  // When the session was last updated

        // Navigation property for related messages
        public ICollection<message> messages { get; set; }
    }
}
