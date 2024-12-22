using Microsoft.EntityFrameworkCore;
using Recipe_generator.Models.Entities;

namespace Recipe_generator.data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        public DbSet<message> Messages { get; set; }
        public DbSet<session> Sessions { get; set; }

        public DbSet<GroceryItem> GroceryItems { get; set; }


        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure session entity
            modelBuilder.Entity<session>()
                .HasKey(s => s.SessionId);

            modelBuilder.Entity<session>()
                .Property(s => s.CreatedAt)
                .HasDefaultValueSql("GETUTCDATE()");

            modelBuilder.Entity<session>()
                .Property(s => s.LastUpdatedAt)
                .HasDefaultValueSql("GETUTCDATE()");

            // Configure message entity
            modelBuilder.Entity<message>()
                .HasKey(m => m.MessageId);

            modelBuilder.Entity<message>()
                .Property(m => m.CreatedAt)
                .HasDefaultValueSql("GETUTCDATE()");

            // Define the one-to-many relationship
            modelBuilder.Entity<message>()
                .HasOne(m => m.Session)  // A message belongs to a session
                .WithMany(s => s.messages)  // A session has many messages
                .HasForeignKey(m => m.SessionId)  // Foreign key in the message table
                .OnDelete(DeleteBehavior.Cascade);  // Cascade delete messages when session is deleted
        }
    }
}
