using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;

namespace Recipe_generator.Models.Entities
{
    public class message
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int MessageId { get; set; }  // Unique identifier for the message

        [Required]
        public Guid SessionId { get; set; }  // Foreign key linking to the Session table

        [Required]
        public string Role { get; set; }  // Role of the sender (user/assistant)

        [Required]
        public string Content { get; set; }  // Message content

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;  // When the message was created

        // Navigation property for the related session
        [ForeignKey(nameof(SessionId))]
        public session Session { get; set; }

    }
}
