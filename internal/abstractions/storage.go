package abstractions

import (
	"time"

	"github.com/eval-hub/eval-hub/pkg/api"
)

type Storage interface {
	// This is used to identify the storage implementation in the logs and error messages
	GetDatasourceName() string

	Ping(timeout time.Duration) error

	// Evaluation job operations
	CreateEvaluationJob(evaluation *api.EvaluationJobConfig) (*api.EvaluationJobResource, error)
	GetEvaluationJob(id string) (*api.EvaluationJobResource, error)
	GetEvaluationJobs(limit int, offset int, statusFilter string) ([]api.EvaluationJobResource, error)
	DeleteEvaluationJob(id string, hardDelete bool) error
	UpdateEvaluationJobStatus(id string, state *api.StatusEvent) error

	// Collection operations
	CreateCollection(collection *api.CollectionResource) error
	GetCollection(id string, summary bool) (*api.CollectionResource, error)
	GetCollections(limit int, offset int) ([]api.CollectionResource, error)
	UpdateCollection(collection *api.CollectionResource) error
	DeleteCollection(id string) error

	// Close the storage connection
	Close() error
}
